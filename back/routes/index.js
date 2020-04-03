var express = require('express');
var router = express.Router();
var model = require('../model');

/* GET home page. */
router.get('/', function (req, res, next) {
  model.connect(function (db) {
    db.collection('users').find().toArray(function (err, result) {
      console.log('用户列表', result);
      res.render('index', { title: 'Express' });
    })
  })
});

//渲染注册页
// router.get('/regist', function (req, res, next) {
//   res.render('regist', {})
// })
router.get('/regist', function (req, res, next) {
  res.render('regist', {})
})

module.exports = router;
