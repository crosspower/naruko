export default function (client) {
  return {
    login(email, password) {
      const data = {
        email,
        password
      }
      return client.post('/api/auth/', data)
    },
    verify(token) {
      return client.post('/api/auth/verify/', {token})
    },
    refresh(token) {
      return client.post('/api/auth/refresh/', {token})
    },
    reset(email){
      return client.post('/api/auth/reset/', {email})
    }
  }
}