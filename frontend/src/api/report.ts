import client from './client'

interface GeneratedReportResponse {
  data: {
    id: number
    assessment_id: number
  }
}

export function getGeneratedReportId(response: GeneratedReportResponse): number {
  return response.data.id
}

export function generateReport(assessmentId: number) {
  return client.post(`/reports/generate/${assessmentId}`)
}

export function getReport(reportId: number) {
  return client.get(`/reports/${reportId}`)
}

export function listReports(page = 1, pageSize = 20) {
  return client.get('/reports/', { params: { page, page_size: pageSize } })
}

export function shareReport(reportId: number) {
  return client.post(`/reports/${reportId}/share`)
}

export function viewSharedReport(token: string) {
  return client.get(`/reports/shared/${token}`)
}
