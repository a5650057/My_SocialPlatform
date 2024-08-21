# My_SocialPlatform
A social media platform built with Vue 3, Flask, and Redis, featuring user registration, following system, posts, and Fan-out on write, all containerized with Docker.


先使用後端的read.me裝好虛擬環境以及套件

再來到主目錄
```
docker-compose up
```
建好容器之後(須先自行安裝docker desktop)，進入phpmyadmin(預設為127.0.0.1)，
建立database : social_platform，
進入social_platform，
輸入SQL語法，

1. users 表

```sql

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

2. posts 表
```sql

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);
```

3. post_images 表
```sql

CREATE TABLE post_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    image_url TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

```

4. follows 表
```sql

CREATE TABLE follows (
    follower_id VARCHAR(255) NOT NULL,
    followed_id VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (followed_id) REFERENCES users(email) ON DELETE CASCADE
);
```

5. comments 表
```sql

CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

```

接著即可執行


