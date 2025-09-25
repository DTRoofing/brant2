// Database utilities and Prisma client
// This file provides database connection and utility functions

import { PrismaClient } from '@prisma/client'

// Create a singleton Prisma client
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

// Database utility functions
export const dbUtils = {
  /**
   * Test database connection
   */
  async testConnection() {
    try {
      await prisma.$connect()
      return { success: true, message: 'Database connected successfully' }
    } catch (error) {
      console.error('Database connection failed:', error)
      return { success: false, message: 'Database connection failed', error }
    }
  },

  /**
   * Get database health status
   */
  async getHealth() {
    try {
      await prisma.$queryRaw`SELECT 1`
      return { status: 'healthy', timestamp: new Date().toISOString() }
    } catch (error) {
      console.error('Database health check failed:', error)
      return { status: 'unhealthy', timestamp: new Date().toISOString(), error: error.message }
    }
  },

  /**
   * Close database connection
   */
  async disconnect() {
    try {
      await prisma.$disconnect()
      return { success: true, message: 'Database disconnected successfully' }
    } catch (error) {
      console.error('Database disconnection failed:', error)
      return { success: false, message: 'Database disconnection failed', error }
    }
  }
}

// Export Prisma client as default
export default prisma
