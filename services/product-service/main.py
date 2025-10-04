from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import uvicorn
import structlog
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Logging setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

app = FastAPI(title="Product Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
database = client.products
collection = database.products

# Pydantic models
class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    inventory: int = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=50)

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    inventory: int
    sku: str
    created_at: datetime
    updated_at: datetime

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    inventory: Optional[int] = Field(None, ge=0)

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Helper functions
def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "price": product["price"],
        "category": product["category"],
        "inventory": product["inventory"],
        "sku": product["sku"],
        "created_at": product["created_at"],
        "updated_at": product["updated_at"]
    }

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In a real application, verify JWT token here
    # For demo purposes, we'll accept any token
    return {"user_id": "demo_user"}

# Health check
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "service": "product-service",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Get all products
@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 100
):
    try:
        query = {}
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        if min_price is not None:
            query["price"] = {"$gte": min_price}
        if max_price is not None:
            if "price" in query:
                query["price"]["$lte"] = max_price
            else:
                query["price"] = {"$lte": max_price}

        products_cursor = collection.find(query).skip(skip).limit(limit)
        products = await products_cursor.to_list(length=limit)
        
        logger.info("Products retrieved", count=len(products), query=query)
        return [product_helper(product) for product in products]
    except Exception as e:
        logger.error("Error retrieving products", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Get product by ID
@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        product = await collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        logger.info("Product retrieved", product_id=product_id)
        return product_helper(product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving product", product_id=product_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Create product
@app.post("/api/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product, user=Depends(verify_token)):
    try:
        # Check if SKU already exists
        existing_product = await collection.find_one({"sku": product.sku})
        if existing_product:
            raise HTTPException(status_code=409, detail="Product with this SKU already exists")
        
        product_dict = product.dict()
        product_dict["created_at"] = datetime.utcnow()
        product_dict["updated_at"] = datetime.utcnow()
        
        result = await collection.insert_one(product_dict)
        new_product = await collection.find_one({"_id": result.inserted_id})
        
        logger.info("Product created", product_id=str(result.inserted_id), sku=product.sku)
        return product_helper(new_product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating product", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Update product
@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate, user=Depends(verify_token)):
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        # Check if product exists
        existing_product = await collection.find_one({"_id": ObjectId(product_id)})
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = {k: v for k, v in product_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")
        
        updated_product = await collection.find_one({"_id": ObjectId(product_id)})
        
        logger.info("Product updated", product_id=product_id, fields=list(update_data.keys()))
        return product_helper(updated_product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating product", product_id=product_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Delete product
@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, user=Depends(verify_token)):
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID")
        
        result = await collection.delete_one({"_id": ObjectId(product_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        logger.info("Product deleted", product_id=product_id)
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting product", product_id=product_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Search products
@app.get("/api/products/search", response_model=List[ProductResponse])
async def search_products(q: str, skip: int = 0, limit: int = 50):
    try:
        query = {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
                {"sku": {"$regex": q, "$options": "i"}}
            ]
        }
        
        products_cursor = collection.find(query).skip(skip).limit(limit)
        products = await products_cursor.to_list(length=limit)
        
        logger.info("Product search performed", query=q, results=len(products))
        return [product_helper(product) for product in products]
    except Exception as e:
        logger.error("Error searching products", query=q, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3002)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
