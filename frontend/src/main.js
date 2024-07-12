import Vue from "vue";
import VueToast from "vue-toast-notification";
import "vue-toast-notification/dist/theme-bootstrap.css";
import VueDarkMode from "@growthbunker/vuedarkmode";
import App from "./App.vue";
import vuetify from "./plugins/vuetify";
import router from "./router";
import axios from "axios";

Vue.config.productionTip = false;

Vue.use(VueDarkMode, {
  theme: "dark",
});

const http = axios.create({
  // baseURL: "http://127.0.0.1:5000",
  baseURL: "http://127.0.0.1:8080/api", // 使用 NGINX 反向代理後的路徑
  timeout: 10000,
});

http.interceptors.request.use(
  function (config) {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

http.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      if (router.currentRoute.path !== "/login") {
        router.push("/login");
      }
    }
    return Promise.reject(error);
  }
);

Vue.prototype.$http = http;

Vue.use(VueToast, {
  position: "top",
});

new Vue({
  router,
  vuetify,
  VueToast,
  VueDarkMode,
  render: (h) => h(App),
}).$mount("#app");
