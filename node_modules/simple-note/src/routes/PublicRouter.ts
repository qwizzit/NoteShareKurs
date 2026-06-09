import LogInWithEmail from "@src/components/auth/LogInWithEmail.vue";
import LogInWithPassword from "@src/components/auth/LogInWithPassword.vue";
import SignUp from "@src/components/auth/SignUp.vue";
import PublicPage from "@src/components/pages/PublicPage.vue";
import { createRouter, createWebHistory } from "vue-router";

export const PublicRouter = createRouter({
  history: createWebHistory(),
  routes: [
    {
      name: 'PublicPage',
      path: '/',
      component: PublicPage,
      children: [
        {
          name: 'LogWithEmail',
          path: '/login',
          component: LogInWithEmail,
        },
        {
          name: 'LogWithPass',
          path: '/login-with-password',
          component: LogInWithPassword,
        },
        {
          name: 'SignUp',
          path: '/signup',
          component: SignUp,
        }
      ]
    },

    {
      path: '',
      redirect: '/login-with-password',
    }
  ]
});