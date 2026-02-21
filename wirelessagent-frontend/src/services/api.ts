import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const API_BASE_URL = 'http://localhost:8000'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 600000,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    this.client.interceptors.response.use(
      (response) => {
        return response
      },
      (error) => {
        console.error('API Error:', error)
        return Promise.reject(error)
      }
    )
  }

  async uploadCSV(file: File, onProgress?: (progress: number) => void): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    }

    try {
      const response: AxiosResponse = await this.client.post('/upload-csv', formData, config)
      return response.data
    } catch (error) {
      console.error('CSV upload failed:', error)
      throw error
    }
  }

  async processCSV(file: File, onProgress?: (progress: number) => void): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    }

    try {
      const response: AxiosResponse = await this.client.post('/process-csv', formData, config)
      return response.data
    } catch (error) {
      console.error('CSV processing failed:', error)
      throw error
    }
  }

  async getResults(): Promise<any> {
    try {
      const response: AxiosResponse = await this.client.get('/results')
      return response.data
    } catch (error) {
      console.error('Failed to get results:', error)
      throw error
    }
  }
}

export default new ApiService()
