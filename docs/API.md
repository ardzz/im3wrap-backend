# IM3Wrap Backend API Documentation

## Overview

The IM3Wrap Backend API provides a comprehensive set of endpoints for managing user accounts, IM3 service integration, and data package purchases. This RESTful API is built with Flask and follows modern API design principles.

## Base URL

- **Production**: `https://backend.im3wrap.my.id/api`
- **Development**: `http://localhost:5000/api`

## Authentication

Most endpoints require JWT authentication. After logging in, include the JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## API Overview

### Endpoints Summary

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new user | ❌ |
| `/auth/login` | POST | User login | ❌ |
| `/user/me` | GET | Get user profile | ✅ |
| `/user/me` | PUT | Update user profile | ✅ |
| `/user/me/change-password` | POST | Change password | ✅ |
| `/im3/send-otp` | GET | Send OTP to phone | ✅ |
| `/im3/verify-otp` | POST | Verify OTP code | ✅ |
| `/im3/profile` | GET | Get IM3 profile | ✅ |
| `/packages/packages` | GET | List packages | ✅ |
| `/packages/packages/purchase` | POST | Purchase package | ✅ |
| `/packages/transactions` | GET | Get transactions | ✅ |
| `/packages/transactions/{id}` | GET | Get transaction status | ✅ |
| `/health` | GET | Health check | ❌ |

## Authentication Flow

### 1. User Registration

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "req_123456789",
  "timestamp": "2025-05-31T09:44:01Z",
  "data": {
    "user_id": 1,
    "username": "john_doe",
    "message": "User registered successfully"
  },
  "message": "User registered successfully",
  "meta": {}
}
```

### 2. User Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "req_123456789",
  "timestamp": "2025-05-31T09:44:01Z",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": null
    },
    "message": "Login successful"
  },
  "message": "Login successful",
  "meta": {}
}
```

## IM3 Integration Flow

### 1. Update Phone Number

First, ensure your phone number is set in your profile:

```http
PUT /api/user/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "phone_number": "628123456789"
}
```

### 2. Send OTP

```http
GET /api/im3/send-otp
Authorization: Bearer <token>
```

### 3. Verify OTP

```http
POST /api/im3/verify-otp
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "123456"
}
```

### 4. Get IM3 Profile

```http
GET /api/im3/profile
Authorization: Bearer <token>
```

## Package Purchase Flow

### 1. List Available Packages

```http
GET /api/packages/packages
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "pvr_code": "IM3001",
      "keyword": "DATA5GB",
      "discount_price": 45000,
      "normal_price": 50000,
      "package_name": "5GB Internet Package",
      "created_at": "2025-05-31T09:00:00Z",
      "updated_at": "2025-05-31T09:00:00Z"
    }
  ]
}
```

### 2. Purchase Package

```http
POST /api/packages/packages/purchase
Authorization: Bearer <token>
Content-Type: application/json

{
  "package_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": 1,
    "task_id": "task_abc123",
    "package_detail": {
      "id": 1,
      "package_name": "5GB Internet Package",
      "discount_price": 45000
    },
    "message": "Transaction is being processed",
    "status": "PENDING"
  }
}
```

### 3. Check Transaction Status

```http
GET /api/packages/transactions/1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 1,
    "package_id": 1,
    "status": "PAYMENT_INITIATED",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "created_at": "2025-05-31T09:00:00Z",
    "updated_at": "2025-05-31T09:30:00Z"
  }
}
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "request_id": "req_123456789",
  "timestamp": "2025-05-31T09:44:01Z",
  "data": {},
  "message": "Operation successful",
  "meta": {}
}
```

### Error Response
```json
{
  "success": false,
  "request_id": "req_123456789",
  "timestamp": "2025-05-31T09:44:01Z",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "username": ["Username is required"]
    }
  }
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `AUTHENTICATION_ERROR` | Authentication required/failed | 401 |
| `AUTHORIZATION_ERROR` | Access denied | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `CONFLICT` | Resource conflict | 409 |
| `BUSINESS_LOGIC_ERROR` | Business rule violation | 422 |
| `EXTERNAL_SERVICE_ERROR` | External service error | 502 |
| `USERNAME_EXISTS` | Username already taken | 409 |
| `INVALID_CREDENTIALS` | Wrong username/password | 401 |
| `USER_NOT_FOUND` | User not found | 404 |
| `PACKAGE_NOT_FOUND` | Package not found | 404 |
| `IM3_AUTH_ERROR` | IM3 service error | 502 |

## Transaction Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Transaction created, processing not started |
| `PROCESSING` | Transaction being processed |
| `CHECKING_ELIGIBILITY` | Checking package eligibility |
| `WAITING_FOR_ELIGIBILITY` | Waiting for eligibility confirmation |
| `INITIATING_PAYMENT` | Initiating payment process |
| `PAYMENT_INITIATED` | Payment QR code generated |
| `COMPLETED` | Transaction completed successfully |
| `FAILED` | Transaction failed |
| `CANCELLED` | Transaction cancelled |

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **IM3 endpoints**: 10 requests per minute per user
- **Package endpoints**: 20 requests per minute per user
- **Other endpoints**: 60 requests per minute per user

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'john_doe',
    'password': 'password123'
})
token = response.json()['data']['access_token']

# Get packages
headers = {'Authorization': f'Bearer {token}'}
packages = requests.get('http://localhost:5000/api/packages/packages', headers=headers)
print(packages.json())
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password123'
  })
});
const { data } = await loginResponse.json();
const token = data.access_token;

// Get packages
const packagesResponse = await fetch('http://localhost:5000/api/packages/packages', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const packages = await packagesResponse.json();
console.log(packages);
```

### cURL
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"password123"}'

# Get packages (replace TOKEN with actual token)
curl -X GET http://localhost:5000/api/packages/packages \
  -H "Authorization: Bearer TOKEN"
```

## Testing

### Using Postman

1. Import the OpenAPI spec from `/docs/openapi.yaml`
2. Set up environment variables:
   - `base_url`: `http://localhost:5000/api`
   - `token`: (set after login)

### Using Swagger UI

Access the interactive API documentation at:
- Development: `http://localhost:5000/docs`
- Production: `https://backend.im3wrap.my.id/docs`

## Support

For API support, please contact:
- Email: support@im3wrap.my.id
- Documentation: https://docs.im3wrap.my.id
- GitHub Issues: https://github.com/ardzz/im3wrap-backend/issues