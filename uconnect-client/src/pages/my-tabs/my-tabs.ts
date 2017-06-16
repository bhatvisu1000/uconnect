import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { MySchedulePage } from '../my-schedule/my-schedule';
import { MyActivityPage } from '../my-activity/my-activity';
import { MyConnectionPage } from '../my-connection/my-connection';
import { MyNotificationPage } from '../my-notification/my-notification';
import { MyOffersPage } from '../my-offers/my-offers';

@Component({
  selector: 'page-my-tabs',
  template: `<ion-tabs>
     
     <ion-tab tabIcon="people" tabTitle="Connection" [root]="myConnectionPage"></ion-tab>
     <ion-tab tabIcon="calendar" tabTitle="Schedule" [root]="mySchedulePage"></ion-tab>
     <ion-tab tabIcon="pulse" tabTitle="Activity" [root]="myActivityPage"></ion-tab>
     <ion-tab tabIcon="flag" tabTitle="Notification" [root]="myNotificationPage"></ion-tab>
     <ion-tab tabIcon="cash" tabTitle="Offers" [root]="myOffersPage" tabBadge="4" tabBadgeStyle="danger"></ion-tab>
     

   </ion-tabs>`
})

export class MyTabsPage {
mySchedulePage = MySchedulePage;
myActivityPage = MyActivityPage;
myConnectionPage = MyConnectionPage;
myNotificationPage = MyNotificationPage;
myOffersPage = MyOffersPage;


  constructor(public navCtrl: NavController, public navParams: NavParams) {


  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad MyTabsPage');
  }

}
