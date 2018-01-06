import { Component, ViewChild } from '@angular/core';
import { Events, MenuController, Nav, Platform  } from 'ionic-angular';
import { SplashScreen } from '@ionic-native/splash-screen';

import { Storage } from '@ionic/storage';

import { MyTabsPage } from '../pages/my-tabs/my-tabs';

import { MySchedulePage } from '../pages/my-schedule/my-schedule';
import { MyActivityPage } from '../pages/my-activity/my-activity';
import { MyConnectionPage } from '../pages/my-connection/my-connection';
import { MyNotificationPage } from '../pages/my-notification/my-notification';
import { MyOffersPage } from '../pages/my-offers/my-offers';
import { LoginPage } from '../pages/login/login';


import { RegistrationPage } from '../pages/registration/registration';

import { AuthService } from "../services/AuthService";
import { RegistrationService } from "../services/RegistrationService";

export interface PageInterface {
  title: string;
  name: string;
  component: any;
  icon: string;
  logsOut?: boolean;
  index?: number;
  tabName?: string;
  tabComponent?: any;
}


@Component({
  templateUrl: 'app.html'
})

export class MyApp {
  // the root nav is a child of the root app component
  // @ViewChild(Nav) gets a reference to the app's root nav
  @ViewChild(Nav) nav: Nav;

  // List of pages that can be navigated to from the left menu
  // the left menu only works after login
  // the login page disables the left menu
  appPages: PageInterface[] = [
    { title: 'Schedule', name: 'TabsPage', component: MyTabsPage, tabComponent: MySchedulePage, index: 0, icon: 'calendar' },
    { title: 'Connection', name: 'TabsPage', component: MyTabsPage, tabComponent: MyConnectionPage, index: 1, icon: 'people' },
    { title: 'Activity', name: 'TabsPage', component: MyTabsPage, tabComponent: MyActivityPage, index: 2, icon: 'pulse' },
    
    { title: 'Notification', name: 'TabsPage', component: MyTabsPage, tabComponent: MyNotificationPage, index: 3, icon: 'flag' }
  ];
  loggedInPages: PageInterface[] = [
    { title: 'Settings', name: 'AccountPage', component: RegistrationPage, icon: 'person' },
    { title: 'Logout', name: 'MyTabsPage', component: MyTabsPage, icon: 'log-out', logsOut: true }
  ];
  loggedOutPages: PageInterface[] = [
        { title: 'Login People', name: 'Login', component: LoginPage, icon: 'log-in' },
        { title: 'Signup', name: 'Registration', component: RegistrationPage, icon: 'person-add' }

  ];
  rootPage: any;

  constructor(
    public events: Events,
    public authService: AuthService,
    public menu: MenuController,
    public platform: Platform,
    public registrationService: RegistrationService,
    public storage: Storage,
    public splashScreen: SplashScreen
  ) {

    // Check if the user has already seen the tutorial
    
    this.rootPage = LoginPage;
    this.platformReady()

    // load the conference data
    /**confData.load();**/

    // decide which menu items should be hidden by current login status stored in local storage
    this.authService.hasLoggedIn().then((hasLoggedIn) => {
      this.enableMenu(hasLoggedIn === true);
    });
    this.enableMenu(true);

    this.listenToLoginEvents();
  }

  openPage(page: PageInterface) {
    let params = {};

    // the nav component was found using @ViewChild(Nav)
    // setRoot on the nav to remove previous pages and only have this page
    // we wouldn't want the back button to show in this scenario
    if (page.index) {
      params = { tabIndex: page.index };
    }

    // If we are already on tabs just change the selected tab
    // don't setRoot again, this maintains the history stack of the
    // tabs even if changing them from the menu
    if (this.nav.getActiveChildNav() && page.index != undefined) {
      this.nav.getActiveChildNav().select(page.index);
    // Set the root of the nav with params if it's a tab index
  } else {
      this.nav.setRoot(page.name, params).catch((err: any) => {
        console.log(`Didn't set nav root: ${err}`);
      });
    }

    if (page.logsOut === true) {
      // Give the menu time to close before changing to logged out
      this.authService.logout();
      this.nav.setRoot(LoginPage);
    }
  }

  listenToLoginEvents() {
    this.events.subscribe('user:login', () => {
      this.enableMenu(true);
    });

    this.events.subscribe('user:signup', () => {
      this.enableMenu(true);
    });

    this.events.subscribe('user:logout', () => {
      this.enableMenu(false);
    });
  }

  enableMenu(loggedIn: boolean) {
    this.menu.enable(loggedIn, 'loggedInMenu');
    this.menu.enable(!loggedIn, 'loggedOutMenu');
  }

  platformReady() {
    // Call any initial plugins when ready
    this.platform.ready().then(() => {
      this.splashScreen.hide();
    });
  }

  isActive(page: PageInterface) {
    let childNav = this.nav.getActiveChildNav();

    // Tabs are a special case because they have their own navigation
    if (childNav) {
      if (childNav.getSelected() && childNav.getSelected().root === page.tabName) {
        return 'primary';
      }
      return;
    }

    if (this.nav.getActive() && this.nav.getActive().name === page.name) {
      return 'primary';
    }
    return;
  }
}

