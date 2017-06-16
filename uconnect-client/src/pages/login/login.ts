import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';

import { NavController } from 'ionic-angular';

import { AuthService } from "../../services/AuthService";

import { MyTabsPage } from '../my-tabs/my-tabs';
import { RegistrationPage } from '../registration/registration';
import {ResponseReceived} from "../../models/ResponseReceived"
import { MyConnectionPage } from '../my-connection/my-connection';
import {Observable} from 'rxjs/Observable';

@Component({
  selector: 'page-user',
  templateUrl: 'login.html'
})
export class LoginPage {
  login: {username?: string, password?: string} = {};
  submitted = false;
  

  constructor(public navCtrl: NavController, public authService: AuthService) { }

  onLogin(form: NgForm) {
    
    this.submitted = true;

    if (form.valid) {
      this.authService.login(this.login.username, this.login.password);

      this.navCtrl.push(MyTabsPage);
    }
  }


  onSignup() {
    this.navCtrl.push(RegistrationPage);
  }
}
