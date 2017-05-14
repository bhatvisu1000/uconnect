import { Component } from '@angular/core';
import { NgForm } from "@angular/forms";
import { NavController, NavParams } from 'ionic-angular';

import {Member} from "../../models/member/Member"
import { RegisterationService } from "../../services/RegisterationService";
import { MyTabsPage } from '../my-tabs/my-tabs';

@Component({
  selector: 'page-registration',
  templateUrl: 'registration.html'
})

export class RegistrationPage {

  constructor(public navCtrl: NavController, private registerationService: RegisterationService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad RegistrationPage');
  }

  

  onAddMember(form: NgForm) {
    console.log('before create Member RegistrationPage');
    this.registerationService.createMember(form.value.userId, form.value.password, form.value.firstName, form.value.lastName, form.value.zipCode);
    console.log('before submit RegistrationPage');
    this.registerationService.submitMember();
    console.log('before after RegistrationPage');
    this.navCtrl.push(MyTabsPage);
  }
}
