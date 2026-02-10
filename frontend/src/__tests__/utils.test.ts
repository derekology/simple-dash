import { describe, it, expect } from 'vitest'

describe('Utility Functions', () => {
  describe('formatNumber', () => {
    it('formats numbers with commas', () => {
      const formatNumber = (num: number | null) => {
        if (num === null || num === undefined) return 'N/A'
        return num.toLocaleString('en-US')
      }

      expect(formatNumber(1000)).toBe('1,000')
      expect(formatNumber(1000000)).toBe('1,000,000')
      expect(formatNumber(null)).toBe('N/A')
    })
  })

  describe('formatPercent', () => {
    it('formats percentages correctly', () => {
      const formatPercent = (num: number | null) => {
        if (num === null || num === undefined) return 'N/A'
        return `${num.toFixed(1)}%`
      }

      expect(formatPercent(25.5)).toBe('25.5%')
      expect(formatPercent(0.123)).toBe('0.1%')
      expect(formatPercent(null)).toBe('N/A')
    })
  })

  describe('calculateCTOR', () => {
    it('calculates click-to-open rate', () => {
      const calculateCTOR = (clicks: number | null, opens: number | null) => {
        if (clicks === null || clicks === undefined || opens === null || opens === undefined || opens === 0) return null
        return (clicks / opens) * 100
      }

      expect(calculateCTOR(50, 250)).toBeCloseTo(20.0, 1)
      expect(calculateCTOR(0, 250)).toBe(0)
      expect(calculateCTOR(50, 0)).toBe(null)
      expect(calculateCTOR(null, 250)).toBe(null)
    })
  })

  describe('detectOutliers', () => {
    it('detects outliers using IQR method', () => {
      const detectOutliers = (values: number[]) => {
        if (values.length < 4) return []

        const sorted = [...values].sort((a, b) => a - b)
        const q1Index = Math.floor(sorted.length * 0.25)
        const q3Index = Math.floor(sorted.length * 0.75)
        const q1 = sorted[q1Index]!
        const q3 = sorted[q3Index]!
        const iqr = q3 - q1

        const lowerBound = q1 - 1.5 * iqr
        const upperBound = q3 + 1.5 * iqr

        return values
          .map((v, i) => ({ v, i }))
          .filter((item) => item.v < lowerBound || item.v > upperBound)
          .map((item) => item.i)
      }

      const values = [10, 12, 13, 15, 100] // 100 is outlier
      const outliers = detectOutliers(values)
      expect(outliers).toContain(4) // Index of 100
    })
  })

  describe('detectLowVolume', () => {
    it('detects campaigns with low delivery volume', () => {
      const detectLowVolume = (values: number[]) => {
        if (values.length < 2) return []

        const sorted = [...values].sort((a, b) => a - b)
        const mid = Math.floor(sorted.length / 2)
        const median =
          sorted.length % 2 === 0
            ? ((sorted[mid - 1] ?? 0) + (sorted[mid] ?? 0)) / 2
            : sorted[mid] ?? 0

        const threshold = median * 0.5

        return values
          .map((v, i) => ({ v, i }))
          .filter((item) => item.v > 0 && item.v < threshold)
          .map((item) => item.i)
      }

      const values = [100, 200, 300, 40] // 40 is low volume (< 50% of median 150)
      const lowVolume = detectLowVolume(values)
      expect(lowVolume).toContain(3) // Index of 40
    })
  })
})
