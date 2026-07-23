import client from './client'

export function startAssessment() {
  return client.post('/assessment/start', null, {
    responseType: 'stream',
    headers: { 'Accept': 'text/event-stream' },
  })
}

export function submitAnswer(assessmentId: number, questionId: string, answerValue: number, sessionId?: string) {
  return client.post(`/assessment/${assessmentId}/answer`, {
    question_id: questionId,
    answer_value: answerValue,
    session_id: sessionId,
  }, {
    responseType: 'stream',
    headers: { 'Accept': 'text/event-stream' },
  })
}

export function getProgress(assessmentId: number) {
  return client.get(`/assessment/${assessmentId}/progress`)
}

export function bindAssessment(assessmentId: number) {
  return client.post(`/assessment/${assessmentId}/bind`)
}
