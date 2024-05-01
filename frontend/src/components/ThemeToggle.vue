<template>
  <v-btn icon @click="toggleTheme">
    <v-icon>{{ icon }}</v-icon>
  </v-btn>
</template>

<script>
export default {
  data() {
    return {
      icon: this.$vuetify.theme.dark
        ? "mdi-weather-night"
        : "mdi-white-balance-sunny",
    };
  },
  methods: {
    toggleTheme() {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
      this.icon = this.$vuetify.theme.dark
        ? "mdi-weather-night"
        : "mdi-white-balance-sunny";
    },
  },
};
</script>
