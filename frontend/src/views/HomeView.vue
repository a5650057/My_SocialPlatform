<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar dense flat color="grey">
            <v-toolbar-title class="white--text">HUH?</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-container>
              <v-row justify="center">
                <v-btn
                  depressed
                  color="grey lighten-1"
                  class="ma-2 black--text"
                  @click="gotoLogin"
                  >登入</v-btn
                >
                <v-btn
                  depressed
                  color="grey lighten-1"
                  class="ma-2 black--text"
                  @click="gotoRegister"
                  >註冊</v-btn
                >
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  methods: {
    gotoLogin() {
      this.$router.push("/login");
    },
    gotoRegister() {
      this.$router.push("/register");
    },
  },
};
</script>

<style scoped>
/* 添加自定义样式以实现简洁风格 */
.v-btn {
  border: 2px solid white !important; /* 给按钮添加白色边框 */
}
</style>
