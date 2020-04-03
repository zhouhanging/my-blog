<template>
  <div id="info">
    <p>
      <label for="#">昵称:</label>
      <input type="text" />
    </p>
    <p>
      <label for="#">签名:</label>
      <input type="text" />
    </p>
    <p>
      <label for="#">性别:</label>
      <input type="text" />
    </p>
  </div>
</template>
//v-theme:column="'narrow'"
<script>
import axios from "../axios-auth";
export default {
  name: "show-blogs",
  data() {
    return {
      blogs: [],
      search: ""
    };
  },
  created() {
    // this.$http.get('https://wd1182543348jfzvtq.wilddogio.com/posts.json')
    axios
      .get("/posts.json")
      .then(function(data) {
        return data.data;
      })
      .then(data => {
        var blogsArray = [];
        for (let key in data) {
          data[key].id = key;
          blogsArray.push(data[key]);
        }
        this.blogs = blogsArray;
      });
  },
  computed: {
    filteredBlogs: function() {
      return this.blogs.filter(blog => {
        return blog.title.match(this.search);
      });
    }
  },
  filters: {
    // "to-uppercase":function(value){
    // 	return value.toUpperCase();
    // }
    toUppercase(value) {
      return value.toUpperCase();
    }
  },
  directives: {
    rainbow: {
      bind(el, binding, vnode) {
        // el.style.color = "#" + Math.random().toString(16).slice(2,8);
      }
    }
  }
};
</script>

<style scoped>
#info {
  background-color: rgb(250, 184, 176);
  width: 500px;
  height: 380px;
  margin: 10px auto;
  font-family: cursive;
  color: #f40;
  font-size: 20px;
  border-radius: 20px;
  text-align: center;
}
p {
  margin: 10px auto;
}
input {
  margin: 38px auto;
  height: 30px;
  width: 300px;
  border-radius: 10px;
  font-size: 20px;
  text-indent: 2em;
}
</style>