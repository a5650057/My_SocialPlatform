<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card class="mx-auto" max-width="500">
          <v-card-title class="text-h5"> 使用者列表 </v-card-title>
          <div v-if="errorMsg" style="color: red">{{ errorMsg }}</div>
          <v-list class="v-list-custom-scrollbar">
            <v-list-item v-for="user in recommendedUsers" :key="user.email">
              <v-list-item-content>
                <v-list-item-title>{{ user.username }}</v-list-item-title>
              </v-list-item-content>

              <v-btn
                @click="followUser(user.email)"
                color="blue"
                v-if="!isFollowing(user.email)"
                >追蹤</v-btn
              >
              <v-btn
                @click="unfollowUser(user.email)"
                color="grey"
                v-else-if="isFollowing(user.email)"
                >取消追蹤</v-btn
              >
            </v-list-item>
          </v-list>
          <v-card-actions>
            <v-btn @click="$router.push('/lobby')" color="grey" class="ml-5"
              >看看其他人在做什麼</v-btn
            >
            <v-btn @click="logout" color="grey" class="ml-5">登出</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Vue from "vue";
export default {
  data() {
    return {
      recommendedUsers: [],
      errorMsg: "",
    };
  },

  created() {
    this.fetchFollowingUsers();

    this.fetchRecommendedUsers();
  },
  methods: {
    fetchRecommendedUsers() {
      this.$http
        .get("/users/recommended_users")
        .then((response) => {
          this.recommendedUsers = response.data;
        })
        .catch((error) => {
          console.error(
            "There was an error fetching the recommended users: ",
            error
          );
          this.errorMsg =
            error.response && error.response.data
              ? error.response.data.error
              : "HUH?";
        });
    },
    followUser(followedEmail) {
      const followerEmail = localStorage.getItem("userEmail");
      this.$http
        .post("/users/follow", {
          follower_email: followerEmail,
          followed_email: followedEmail,
        })
        .then(async () => {
          await this.$emit("update");
          await Vue.$toast.success("追蹤成功");
          await this.fetchFollowingUsers();
          await this.fetchRecommendedUsers();
        })
        .catch((error) => {
          console.error("There was an error following the user: ", error);
          this.errorMsg =
            error.response && error.response.data
              ? error.response.data.error
              : "HUH?";
        });
    },

    fetchFollowingUsers() {
      this.$http
        .get("/users/following")
        .then((response) => {
          this.followingUsers = response.data;
        })
        .catch((error) => {
          console.error("Error fetching following users: ", error);
        });
    },

    unfollowUser(followedEmail) {
      this.$http
        .post("/users/unfollow", { followed_email: followedEmail })
        .then(async () => {
          const index = this.followingUsers.indexOf(followedEmail);
          if (index !== -1) {
            this.followingUsers.splice(index, 1);
          }
          await this.fetchRecommendedUsers();
          await Vue.$toast.success("取消追蹤成功");
        })
        .catch((error) => {
          console.error("取消追蹤失败: ", error);
          this.errorMsg =
            error.response && error.response.data
              ? error.response.data.error
              : "Error";
        });
    },

    isFollowing(email) {
      return this.followingUsers.includes(email);
    },

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
