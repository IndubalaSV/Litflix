import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)
  const [userPreferences, setUserPreferences] = useState({})
  const [isNewUser, setIsNewUser] = useState(false)
  const [isRegistration, setIsRegistration] = useState(false)

  // Set up axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          // Set up axios headers for the check
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          const response = await axios.get('http://localhost:8000/api/auth/me')
          setUser(response.data)
          // Ensure isNewUser is false for existing users
          setIsNewUser(false)
          // Force set localStorage flag for existing users
          localStorage.setItem('hasSeenPreferences', 'true')
          console.log('Auth check: Existing user detected, isNewUser set to false')
        } catch (error) {
          console.error('Auth check failed:', error)
          logout()
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [token])

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/login', {
        username,
        password
      })
      
      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      
      // Set up axios headers immediately
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Get user info
      const userResponse = await axios.get('http://localhost:8000/api/auth/me')
      setUser(userResponse.data)
      
      // NUCLEAR OPTION: Existing users are NEVER new users
      setIsNewUser(false)
      setIsRegistration(false) // This is a login, not registration
      // Force set localStorage flag for existing users
      localStorage.setItem('hasSeenPreferences', 'true')
      console.log('Login: isNewUser set to false, isRegistration set to false, hasSeenPreferences set to true')
      
      return { success: true }
    } catch (error) {
      console.error('Login failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('http://localhost:8000/api/auth/register', {
        username,
        email,
        password
      })
      
      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      
      // Set up axios headers immediately
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Get user info
      const userResponse = await axios.get('http://localhost:8000/api/auth/me')
      setUser(userResponse.data)
      
      // Mark as new user and registration
      setIsNewUser(true)
      setIsRegistration(true) // This is a registration
      console.log('Register: isNewUser set to true, isRegistration set to true')
      
      // Show preferences modal immediately after successful registration
      // This will be handled by the LoginModal component
      
      return { success: true }
    } catch (error) {
      console.error('Registration failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setIsNewUser(false)
    setIsRegistration(false)
    localStorage.removeItem('token')
    localStorage.removeItem('hasSeenPreferences')
    delete axios.defaults.headers.common['Authorization']
  }

  const resetNewUserFlag = () => {
    setIsNewUser(false)
  }

  const savePreferences = async (preferences) => {
    try {
      await axios.post('http://localhost:8000/api/auth/preferences', preferences)
      setUserPreferences(preferences)
      return { success: true }
    } catch (error) {
      console.error('Failed to save preferences:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to save preferences' 
      }
    }
  }

  const getPreferences = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/auth/preferences')
      setUserPreferences(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Failed to get preferences:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to get preferences',
        data: {}
      }
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    savePreferences,
    getPreferences,
    userPreferences,
    isNewUser,
    isRegistration,
    resetNewUserFlag,
    isAuthenticated: !!token
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 