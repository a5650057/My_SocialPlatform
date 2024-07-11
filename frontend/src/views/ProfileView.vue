<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card class="mx-auto" max-width="500">

          <v-card-actions>
            <v-btn @click="$router.push('/lobby')" color="grey" class="ml-5"
              >看看其他人在做什麼</v-btn
            >
            <v-btn @click="logout" color="grey" class="ml-5">登出</v-btn>
          </v-card-actions>
        </v-card>
        <div v-if="loading" class="text-center">
          <v-progress-circular indeterminate></v-progress-circular>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      recommendedUsers: [],
      followingUsers: [], // 確保 followingUsers 初始化為空數組
      errorMsg: "",
      loading: false,
    };
  },

  created() {
    this.fetchFollowingUsers();
    this.fetchRecommendedUsers();
  },
  methods: {

    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.v-list-custom-scrollbar {
  max-height: 450px; /* 可以根據需要調整這個高度 */
  overflow-y: auto; /* 啟用垂直滾動 */
}

/* 定義滾動條的樣式 */
.v-list-custom-scrollbar::-webkit-scrollbar {
  width: 10px; /* 滾動條的寬度 */
}

.v-list-custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1; /* 滾動條軌道的顏色 */
}

.v-list-custom-scrollbar::-webkit-scrollbar-thumb {
  background: #888; /* 滾動條本身的顏色 */
}

.v-list-custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555; /* 滾動條在鼠標懸停時的顏色 */
}
</style>
