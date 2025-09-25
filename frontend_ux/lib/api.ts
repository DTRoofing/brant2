// API client utilities
// This file provides API client functions for making requests to the backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

// API client class
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Make a GET request
   */
  async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Make a POST request
   */
  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Make a PUT request
   */
  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Make a DELETE request
   */
  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Upload a file
   */
  async uploadFile<T>(endpoint: string, file: File, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.get('/api/v1/health')
  }
}

// Create and export API client instance
export const apiClient = new ApiClient()

// Export the class for custom instances
export { ApiClient }

// Convenience functions
export const api = {
  /**
   * Get estimates
   */
  async getEstimates() {
    return apiClient.get('/api/v1/estimates')
  },

  /**
   * Get estimate by ID
   */
  async getEstimate(id: string) {
    return apiClient.get(`/api/v1/estimates/${id}`)
  },

  /**
   * Create estimate
   */
  async createEstimate(data: any) {
    return apiClient.post('/api/v1/estimates', data)
  },

  /**
   * Update estimate
   */
  async updateEstimate(id: string, data: any) {
    return apiClient.put(`/api/v1/estimates/${id}`, data)
  },

  /**
   * Delete estimate
   */
  async deleteEstimate(id: string) {
    return apiClient.delete(`/api/v1/estimates/${id}`)
  },

  /**
   * Upload file for processing
   */
  async uploadFile(file: File) {
    return apiClient.uploadFile('/api/v1/upload', file)
  },

  /**
   * Process document
   */
  async processDocument(data: any) {
    return apiClient.post('/api/v1/processing', data)
  },

  /**
   * Get processing status
   */
  async getProcessingStatus(id: string) {
    return apiClient.get(`/api/v1/processing/${id}`)
  },

  /**
   * Export estimate
   */
  async exportEstimate(id: string, format: 'pdf' | 'excel' | 'csv') {
    return apiClient.get(`/api/v1/export/${format}/${id}`)
  },

  /**
   * Get projects
   */
  async getProjects() {
    return apiClient.get('/api/v1/projects')
  },

  /**
   * Create project
   */
  async createProject(data: any) {
    return apiClient.post('/api/v1/projects', data)
  }
}
