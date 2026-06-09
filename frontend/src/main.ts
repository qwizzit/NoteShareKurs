import { MainRouter } from "@src/routes/MainRouter.ts";
import { PublicRouter } from "@src/routes/PublicRouter.ts";
import { createApp } from 'vue'
import '@src/styles/Colors.scss'
import '@src/styles/reset.scss'
import '@src/styles/style.scss'
import '@src/styles/sizes.scss'
import '@src/styles/fonts.scss'
import '@src/styles/frequentVariables.scss'
import App from '@src/components/App.vue'

async function setupRoute() {
  return localStorage.getItem('token') ? MainRouter : PublicRouter;
}

setupRoute()
  .then(router => {
    createApp(App).use(router).mount('#app')
  })

