import Vue from 'vue'
import Router from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import LobbyView from '../views/LobbyView.vue'
import ProfileView from '../views/ProfileView.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'HomeView',
      component: HomeView
    },
    {
        path: '/register',
        name: 'RegisterView',
        component: RegisterView
    },
    {
      path: '/login',
      name: 'LoginView',
      component : LoginView
    },
    {
      path: '/lobby',
      name: 'LobbyView',
      component : LobbyView
    },
    {
      path: '/profile',
      name: 'ProfileView',
      component : ProfileView
    }
    
  ]
})
