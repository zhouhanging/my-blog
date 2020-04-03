<template>
  <div id="login">
    <form action="#">
      <p>
        <label for="user"></label>
        <input type="text" id="user" />
      </p>

      <p>
        <label for="ps"></label>
        <input type="password" id="ps" />
      </p>

      <input type="button" value="登录" />
    </form>
  </div>
</template>

<script>
export default {
  name: "show-blogs",
  data() {
    return {
      blogs: [],
      search: ""
    };
  }
};
</script>
<style scoped>
#login {
  background-color: rgb(252, 196, 176);
  width: 500px;
  height: 380px;
  margin: 100px auto;
  border-radius: 20px;
}
p {
  display: block;
  text-align: center;
  margin: 20px auto;
}
input {
  display: inline-block;
  height: 30px;
  width: 300px;
  margin: 30px;
  border-radius: 10px;
  font-size: 20px;
  text-indent: 1em;
}
input[type="button"] {
  display: block;
  height: 50px;
  width: 60px;
  border-radius: 10px;
  margin: 20px auto;
  text-indent: 0;
}
</style>
