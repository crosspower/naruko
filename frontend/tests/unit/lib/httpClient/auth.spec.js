describe('lib/httpClient/auth', () => {
  it('login', (done) => {
    jest.mock('axios');
    const auth = require('@/lib/httpClient/auth').default

    const email = 'test@test.com'
    const password = 'test'

    const axiosMock = jest.fn()
    axiosMock.post = jest.fn()

    auth(axiosMock).login(email, password)

    expect(axiosMock.post).toHaveBeenCalledWith('/api/auth/', {"email": email, "password": password})
    done()
  })

  it('verify', (done) => {
    jest.mock('axios');
    const auth = require('@/lib/httpClient/auth').default

    const token = 'test_token'

    const axiosMock = jest.fn()
    axiosMock.post = jest.fn()

    auth(axiosMock).verify(token)

    expect(axiosMock.post).toHaveBeenCalledWith('/api/auth/verify/', {token: token})
    done()
  })

  it('refresh', (done) => {
    jest.mock('axios');
    const auth = require('@/lib/httpClient/auth').default

    const token = 'test_token'

    const axiosMock = jest.fn()
    axiosMock.post = jest.fn()

    auth(axiosMock).refresh(token)

    expect(axiosMock.post).toHaveBeenCalledWith('/api/auth/refresh/', {token: token})
    done()
  })

  it('reset', (done) => {
    jest.mock('axios');
    const auth = require('@/lib/httpClient/auth').default

    const email = 'test_mail'

    const axiosMock = jest.fn()
    axiosMock.post = jest.fn()

    auth(axiosMock).reset(email)

    expect(axiosMock.post).toHaveBeenCalledWith('/api/auth/reset/', {email: email})
    done()
  })
})