import axios from 'axios'

export function initAuthFromStorage() {
  const token = localStorage.getItem('token')
  if (token) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete axios.defaults.headers.common.Authorization
  }
}

