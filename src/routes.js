import ShowBlogs from './components/ShowBlogs.vue'
import AddBlog from './components/AddBlog.vue'
import SingleBlog from './components/SingleBlog.vue'
import Login from './components/Login.vue'
import Info from './components/Info.vue'

export default [

	{ path: "/", component: ShowBlogs },
	{ path: "/add", component: AddBlog },
	{ path: "/blog/:id", component: SingleBlog },
	{ path: "/Info", component: Info },
	{ path: "/Login", component: Login }
]