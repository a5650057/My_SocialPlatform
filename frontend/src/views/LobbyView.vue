<template>
  <v-app id="inspire">
    <v-app-bar class="px-3" density="compact" flat>
      <v-avatar
        class="hidden-md-and-up"
        color="grey-darken-1"
        size="32"
      ></v-avatar>

      <v-spacer></v-spacer>

      <v-tabs color="grey-darken-2" centered> </v-tabs>
      <v-spacer></v-spacer>

      <v-avatar
        class="hidden-sm-and-down"
        color="grey-darken-1"
        size="32"
      ></v-avatar>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <v-container>
        <v-row>
          <v-col cols="12" md="2">
            <v-sheet min-height="268" rounded="lg"> </v-sheet>
          </v-col>

          <v-col cols="12" md="8">
            <v-btn @click="dialog = true" class="mb-2 mr-3">新增貼文</v-btn>
            <v-btn @click="$router.push('/profile')" class="mb-2"
              >追蹤頁面</v-btn
            >

            <v-dialog v-model="dialog" persistent max-width="600px">
              <v-card>
                <v-card-title>分享新鲜事</v-card-title>
                <v-card-text>
                  <v-textarea
                    v-model="newPostContent"
                    label="你的故事..."
                    outlined
                  ></v-textarea>
                  <v-file-input
                    v-model="images"
                    accept="image/*"
                    label="選取圖片"
                    outlined
                    dense
                    multiple
                  ></v-file-input>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="blue darken-1" text @click="dialog = false"
                    >CANCEL</v-btn
                  >
                  <v-btn color="blue darken-1" text @click="createPost"
                    >POST</v-btn
                  >
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-card class="mb-2" v-for="post in posts" :key="post.id">
              <v-card-title>
                <div class="d-flex justify-space-between align-center w-100">
                  <span class="blue--text font-weight-bold"
                    >{{ post.username }} :</span
                  >
                </div>
              </v-card-title>
              <v-card-text>{{ post.content }}</v-card-text>
              <div v-if="post.images_urls && post.images_urls.length > 0">
                <v-img
                  v-for="(imageUrl, index) in post.images_urls"
                  :key="index"
                  :src="imageUrl"
                  class="ma-5"
                  aspect-ratio="1.5"
                  @click="openImageDialog(imageUrl)"
                ></v-img>
              </div>

              <v-card-subtitle>{{ post.created_at }}</v-card-subtitle>
              <v-btn
                v-if="post.user_email === userEmail"
                icon
                color="red"
                @click="deletePost(post.id)"
                class="ml-20 mr-2"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </v-card>

            <v-dialog
              v-model="imageDialog"
              persistent
              max-width="600px"
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

          <v-col cols="12" md="2">
            <v-sheet min-height="268" rounded="lg">
              <!--  -->
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      posts: [],
      newPostContent: "",
      dialog: false,
      userEmail: localStorage.getItem("userEmail"),
      images: [],
      imageDialog: false,
      currentImageUrl: "",
    };
  },
  created() {
    this.verifyToken();
    this.fetchPosts();
  },
  methods: {
    openImageDialog(imageUrl) {
      this.currentImageUrl = imageUrl;
      this.imageDialog = true;
    },
    deletePost(postId) {
      this.$http
        .delete(`/posts/posts/${postId}`)
        .then(() => {
          this.$toast.success("Post deleted successfully");
          this.fetchPosts();
        })
        .catch((error) => {
          console.error("Error deleting the post: ", error);
        });
    },

    fetchPosts() {
      this.$http
        .get("/posts/posts")
        .then((response) => {
          this.posts = response.data;
          console.log("Posts data:", response.data); // 这里输出接收到的帖子数据
        })
        .catch((error) => {
          console.log(error);
        });
    },
    createPost() {
      let formData = new FormData();
      formData.append("content", this.newPostContent);
      this.images.forEach((file, index) => {
        formData.append(`image${index}`, file); // 后端需要调整以支持这种命名
      });

      this.$http
        .post("/posts/posts", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        .then(() => {
          this.dialog = false; // 关闭对话框
          this.newPostContent = ""; // 清空内容
          this.images = []; // 清空已选图片
          this.fetchPosts(); // 重新获取帖子列表
        })
        .catch((error) => {
          console.error("创建帖子失败: ", error);
        });
    },

    verifyToken() {
      this.$http
        .get("/users/verify_token")
        .then((response) => {
          console.log(response.data.message);
        })
        .catch((error) => {
          if (error.response) {
            this.$router.push("/");
          }
        });
    },

    goToProfile() {
      this.$router.push("/profile");
    },
    followUser(email) {
      console.log("Following user with email: ", email);
    },
  },
};
</script>
