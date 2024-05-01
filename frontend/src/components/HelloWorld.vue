<template>
  <div>
    <p v-if="message">{{ message }}</p>
    <p v-else>Loading...</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      message: ''
    }
  },
  mounted() {
    axios.get('http://127.0.0.1:5000/huh/example')
      .then(response => {
        this.message = response.data.message
      })
      .catch(error => {
        console.error(error)
      })
  }
}
</script>
