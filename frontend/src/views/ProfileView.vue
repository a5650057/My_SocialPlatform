<template>
  <v-app id="inspire">
    <v-app-bar class="px-3" density="compact" flat>
      <v-btn color="primary" @click="backToLobby">回到大廳</v-btn>
      <v-btn color="error" @click="logout">登出</v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <v-container>
        <v-row>
          <v-col cols="12" md="8" offset-md="2">
            <v-card class="mb-2" v-for="post in posts" :key="post.id">
              <v-card-title>
                <div class="d-flex justify-space-between align-center w-100">
                  <span class="blue--text font-weight-bold">{{ post.username }} :</span>
                </div>
              </v-card-title>
              <v-card-text>{{ post.content }}</v-card-text>
              <v-row v-if="post.images_urls && post.images_urls.length > 0" no-gutters>
                <v-col v-for="(imageUrl, index) in post.images_urls" :key="index" cols="auto">
                  <v-img
                    :src="imageUrl"
                    class="ma-5 image-border"
                    aspect-ratio="1"
                    width="300"
                    height="300"
                    @click="openImageDialog(imageUrl)"
                  ></v-img>
                </v-col>
              </v-row>
              <v-card-subtitle>{{ post.created_at }}</v-card-subtitle>
              <v-list dense>
                <v-subheader>留言</v-subheader>
                <v-list-item v-for="comment in post.comments" :key="comment.id">
                  <v-list-item-content>
                    <v-list-item-title :style="{ fontSize: '20px', fontWeight: 'bold' }">{{ comment.username }}</v-list-item-title>
                    <v-list-item-subtitle>{{ comment.content }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <v-text-field
                label="新增留言..."
                v-model="commentContent[post.id]"
                @keyup.enter="addComment(post.id)"
                outlined
                dense
              ></v-text-field>
            </v-card>

            <v-dialog
              v-model="imageDialog"
              persistent
              max-width="900px"
              @click:outside="imageDialog = false"
            >
              <v-card>
                <v-img :src="currentImageUrl" contain></v-img>
                <v-card-actions>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-col>
        </v-row>
      </v-container>

     
    </v-main>
  </v-app>
</template>

<script>
import axios from 'axios';

axios.defaults.baseURL = 'http://127.0.0.1:8080/api';

export default {
  data() {
    return {
      posts: [],
      commentContent: {},
      userEmail: localStorage.getItem("userEmail"),
      imageDialog: false,
      currentImageUrl: "",
    };
  },
  created() {
    this.fetchUserPosts(); 
  },
  methods: {
    addComment(postId) {
      const comment = this.commentContent[postId];
      if (!comment) return;

      this.$http.post('/posts/comments/add', { post_id: postId, content: comment })
        .then(() => {
          this.commentContent[postId] = ''; // 清空留言輸入框
          this.fetchUserPosts(); // 重新獲取帖子及其留言
        })
        .catch((error) => {
          console.error("新增留言失敗: ", error);
        });
    },

    openImageDialog(imageUrl) {
      this.currentImageUrl = imageUrl;
      this.imageDialog = true;
    },
    fetchUserPosts() {
      console.log("Fetching posts for user");  // 確認 API 調用

      const username = this.$route.params.username; // 獲取路由參數中的用戶名
      if (!username) {
        console.log("沒有找到用戶名");
        return;
      }

      console.log(`Fetching posts for username: ${username}`); // 添加調試信息

      axios
        .get(`/posts/user?username=${username}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        .then((response) => {
          console.log("API response:", response.data);  // 添加調試信息

          if (response.data && response.data.length > 0) {
            this.posts = response.data.map(post => ({
              ...post,
              comments: post.comments || []
            }));
            console.log("User posts data:", this.posts);
          } else {
            console.log("No posts found for this user.");
          }
        })
        .catch((error) => {
          console.log("Error fetching user posts:", error);
        });
    },
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    backToLobby() {
      this.$router.push("/lobby");
    },
  },
};
</script>

<style scoped>
.image-border {
  border: 10px solid #000000; /* 設置邊框顏色和寬度 */
  border-radius: 5px; /* 如果需要圓角，可以設置邊框圓角 */
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* 可選：添加陰影效果 */
}
</style>
