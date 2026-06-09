import MainPage from "@src/components/pages/MainPage.vue";
import { createRouter, createWebHistory } from "vue-router";

export const MainRouter = createRouter({
  history: createWebHistory(),
  routes: [
    {
      name: 'MainPage',
      path: '/',
      component: MainPage,
      children: [
        {
          name: 'Settings',
          path: 'settings',
          component: MainPage // ToDo: сделать нужный компонент с настройками
        },
      ]
    },
    // {
    //   name: 'Collaborate',
    //   path: '/shared',
    //   component: CollabPage,
    //   children: [
    //     {
    //       path: ':id',
    //       component: ActiveNote
    //     }
    //   ]
    // },
    {
      path: '/:catchAuth(login|login-with-password|signup)',
      redirect: '/'
    }
  ]
});