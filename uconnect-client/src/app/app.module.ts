import { NgModule, ErrorHandler } from '@angular/core';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { MyApp } from './app.component';
import { MySchedulePage } from '../pages/my-schedule/my-schedule';
import { MyActivityPage } from '../pages/my-activity/my-activity';
import { MyConnectionPage } from '../pages/my-connection/my-connection';
import { MyNotificationPage } from '../pages/my-notification/my-notification';
import { MyOffersPage } from '../pages/my-offers/my-offers';
import { MyTabsPage } from '../pages/my-tabs/my-tabs';
import { RegistrationPage } from '../pages/registration/registration';

import { ConnectionService } from "../services/ConnectionService";
import { RegisterationService } from "../services/RegisterationService";

@NgModule({
  declarations: [
    MyApp,
    MySchedulePage,
    MyActivityPage,
    MyConnectionPage,
    MyNotificationPage,
    MyOffersPage,
    RegistrationPage,
    MyTabsPage
  ],
  imports: [
    IonicModule.forRoot(MyApp)
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
    MyTabsPage
  ],
  providers: [{provide: ErrorHandler, useClass: IonicErrorHandler},
                ConnectionService, RegisterationService
  ]
})
export class AppModule {}
