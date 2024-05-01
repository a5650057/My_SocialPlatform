<template>
  <v-container>
    <v-form @submit.prevent="register">
      <div v-if="errorMsg" style="color: red">{{ errorMsg }}</div>

      <v-text-field
        v-model="email"
        label="Email"
        :error-messages="emailErrors"
      ></v-text-field>
      <v-text-field
        v-model="username"
        label="Username"
        :error-messages="usernameErrors"
      ></v-text-field>
      <v-text-field
        v-model="password"
        label="Password"
        :error-messages="passwordErrors"
      ></v-text-field>
      <v-btn type="submit" color="primary">註冊</v-btn>
      <v-btn @click="$router.push('/')" color="GREY" class="ml-5"
        >返回首頁</v-btn
      >
    </v-form>
  </v-container>
</template>

<script>
import axios from "axios";
import { API_URL } from "../config.js";

export default {
  data() {
    return {
      email: "",
      username: "",
      password: "",
      errorMsg: "",
      emailErrors: [],
      usernameErrors: [],
      passwordErrors: [],
    };
  },

  methods: {
    validateInput() {
      let isValid = true;
      this.emailErrors = [];
      this.usernameErrors = [];
      this.passwordErrors = [];

      if (this.email.length < 8 || !this.email.includes("@")) {
        this.emailErrors.push(
          'Email must be longer than 8 characters and contain "@"'
        );
        isValid = false;
      }

      // if (
      //   this.username.length < 3 ||
      //   !/[a-zA-Z]/.test(this.username) ||
      //   !/[0-9]/.test(this.username)
      // ) {
      //   this.usernameErrors.push(
      //     "Username must be longer than 3 characters and include both letters and numbers"
      //   );
      //   isValid = false;
      // }

      return isValid;
    },

    register() {
      if (!this.validateInput()) {
        return;
      }
      const userData = {
        email: this.email,
        username: this.username,
        password: this.password,
        created_at: new Date().toISOString().slice(0, 19).replace("T", " "),
      };
      axios
        .post(`${API_URL}/users/register`, userData)
        .then((response) => {
          console.log(response.data);
          this.$toast.success("註冊成功");
          this.$router.push("/");
        })
        .catch((error) => {
          this.errorMsg =
            error.response && error.response.data
              ? error.response.data.errormessage
              : "HUH?";
          console.error(error);
        });
    },
  },
};
</script>
