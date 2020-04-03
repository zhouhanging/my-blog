<template>
  <div id="app">
    <!-- <add-blog></add-blog> -->
    <!-- <show-blogs></show-blogs> -->
    <blog-header></blog-header>
    <router-view></router-view>
  </div>
</template>

<script>
import AddBlog from "./components/AddBlog";
import ShowBlogs from "./components/ShowBlogs";
import BlogHeader from "./components/BlogHeader";
import Login from "./components/Login";
import Info from "./components/Info";

export default {
  name: "app",
  components: {
    AddBlog,
    ShowBlogs,
    BlogHeader,
    Login,
    Info
  }
};
</script>

<style>
* {
  font-family: cursive;
  color: #ff4400;
}
</style>
