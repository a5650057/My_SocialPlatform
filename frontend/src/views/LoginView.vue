<template>
  <v-container>
    <v-form @submit.prevent="login">
      <v-text-field v-model="email" label="Email"></v-text-field>
      <v-text-field
        v-model="password"
        label="Password"
        type="password"
      ></v-text-field>
      <v-btn type="submit" color="primary">登入</v-btn>
      <v-btn
        depressed
        color="grey lighten-1"
        class="ma-2 black--text"
        @click="gotoRegister"
        >還沒註冊?
      </v-btn>
    </v-form>
  </v-container>
</template>

<script>
import axios from "axios";
import { API_URL } from "../config.js";
import Vue from "vue";

export default {
  data() {
    return {
      email: "",
      password: "",
    };
  },
  methods: {
    login() {
      const userData = {
        email: this.email,
        password: this.password,
      };
      axios
        .post(`${API_URL}/users/login`, userData)
        .then((response) => {
          localStorage.setItem("token", response.data.token);
          localStorage.setItem("userEmail", this.email);

          console.log(response.data);
          this.$router.push("/profile");
          Vue.$toast.success("登入成功");
        })
        .catch((error) => {
          if (!error.response || error.response.status === 503) {
            Vue.$toast.error("網站正在維護中");
          } else {
            Vue.$toast.error("帳號或密碼錯誤");
          }
          console.error(error);
        });
    },
    gotoRegister() {
      this.$router.push("/register");
    },
  },
};
</script>
