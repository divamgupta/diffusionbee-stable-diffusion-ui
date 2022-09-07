# Liner Electron App

## Project setup
```
git submodule update --init --recursive
cd third_party/vue-toast-notification
npm install
npm run build   
 cd ../..       
npm install

```

### Compiles and hot-reloads for development
```
 npm run serve:ui  # running the UI elements 
 npm run electron:serve # run via electron 
```

### Compiles and minifies for production
```
npm run build
npm run electron:build
```

for building for production set env  `APPLE_ID` and `APPLE_ID_PASSWORD` 

### Lints and fixes files

```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
