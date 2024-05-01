<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-spacer></v-spacer>
      <theme-toggle />
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import ThemeToggle from "./components/ThemeToggle.vue";

export default {
  name: "App",
  components: {
    ThemeToggle,
  },
  data: () => ({
    //
  }),
};
</script>
