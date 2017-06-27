import { Component } from '@angular/core';
import { NgForm } from '@angular/forms';

import { NavController } from 'ionic-angular';

import { AuthService } from "../../services/AuthService";

import { Storage } from '@ionic/storage';

import { MyTabsPage } from '../my-tabs/my-tabs';
import { RegistrationPage } from '../registration/registration';
import {ResponseReceived} from "../../models/ResponseReceived"
import {MyConnectionPage } from '../my-connection/my-connection';
import {Observable} from 'rxjs/Observable';

import {SendRequest} from "../../models/SendRequest"
import {Data} from "../../models/response/Data"
import {MyResponse} from "../../models/MyResponse"

import {HttpService} from "../../services/HttpService"

import 'rxjs/Rx';

import { Response } from "@angular/http";



@Component({
  selector: 'page-user',
  templateUrl: 'login.html'
})
export class LoginPage {
  login: {username?: string, password?: string} = {};
  submitted = false;
  
  private sendRequest: SendRequest = null;

  constructor(public navCtrl: NavController, public authService: AuthService, private httpService: HttpService, public storage: Storage) { }

  onLogin(form: NgForm) {
    
    this.submitted = true;

    if (form.valid) {
      this.sendRequest = this.authService.login(this.login.username, this.login.password);
      this.httpService.submitRequest(this.authService.sendRequest)
      .subscribe(
        (response: Response) => {
          const responseReceived: ResponseReceived = response.json();
          console.log(responseReceived);
          this.authService.responseReceived=responseReceived;
          this.storage.set('AuthResponse', responseReceived.MyResponse.Data[0]);
          this.navCtrl.push(MyTabsPage);          
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
      
    }
  }


  onSignup() {
    this.navCtrl.push(RegistrationPage);
  }
}
