import { BrowserModule } from '@angular/platform-browser';
import { HttpModule } from '@angular/http';

import { NgModule, ErrorHandler } from '@angular/core';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { IonicStorageModule } from '@ionic/storage';

import { SplashScreen } from '@ionic-native/splash-screen';
import { InAppBrowser } from '@ionic-native/in-app-browser';


import { MyApp } from './app.component';
import { MySchedulePage } from '../pages/my-schedule/my-schedule';
import { MyActivityPage } from '../pages/my-activity/my-activity';
import { MyConnectionPage } from '../pages/my-connection/my-connection';
import { MyCreateSchedulePage } from '../pages/my-create-schedule/my-create-schedule';
import { MyNotificationPage } from '../pages/my-notification/my-notification';
import { MyOffersPage } from '../pages/my-offers/my-offers';
import { MyTabsPage } from '../pages/my-tabs/my-tabs';
import { RegistrationPage } from '../pages/registration/registration';
import { LoginPage } from '../pages/login/login';

import { ConnectionService } from "../services/ConnectionService";
import { RegistrationService } from "../services/RegistrationService";
import { AuthService } from "../services/AuthService";
import { HttpService } from "../services/HttpService";
import { SQLStorageService } from "../services/SQLStorageService";
import { Geolocation } from '@ionic-native/geolocation';




@NgModule({
  declarations: [
    MyApp,
    MySchedulePage,
    MyActivityPage,
    MyConnectionPage,
    MyNotificationPage,
    MyOffersPage,
    RegistrationPage,
    MyTabsPage,
    LoginPage,
    MyCreateSchedulePage
  ],  
  imports: [
    BrowserModule,
    HttpModule,
    IonicModule.forRoot(MyApp, {}, {
      links: [
        { component: MyTabsPage, name: 'Tabs', segment: 'tabs' },
        { component: MySchedulePage, name: 'Schedule', segment: 'schedule' },   
        { component: MyActivityPage, name: 'Activity', segment: 'activity' },
        { component: MyConnectionPage, name: 'Connection', segment: 'connection' },
        { component: MyNotificationPage, name: 'Notification', segment: 'notification' },
        { component: MyOffersPage, name: 'Offers', segment: 'offers' },
        { component: RegistrationPage, name: 'Registration', segment: 'registration' },
        { component: LoginPage, name: 'Login', segment: 'login' }
      ]
    }),
    IonicStorageModule.forRoot()
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp,
    MySchedulePage,
    MyActivityPage,
    MyConnectionPage,
    MyNotificationPage,
    MyOffersPage,
    RegistrationPage,
    MyTabsPage,
    LoginPage,
    MyCreateSchedulePage
  ],
  providers: [{provide: ErrorHandler, useClass: IonicErrorHandler},
                ConnectionService, RegistrationService, AuthService,
    InAppBrowser,
    SplashScreen, HttpService, SQLStorageService,
    Geolocation
  ]
})
export class AppModule {}
