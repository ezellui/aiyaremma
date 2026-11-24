/**
 * Пример теста
 */

const request = require('supertest');
const app = require('../src/app');

describe('Health Check', () => {
  it('should return 200 OK', async () => {
    const response = await request(app).get('/health');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('status', 'healthy');
  });
});

describe('API Root', () => {
  it('should return service info', async () => {
    const response = await request(app).get('/api');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('message');
  });
});

describe('404 Handler', () => {
  it('should return 404 for unknown routes', async () => {
    const response = await request(app).get('/unknown-route');
    
    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
  });
});