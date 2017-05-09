import { Component } from '@angular/core';
import { NgForm } from "@angular/forms";

import {Member} from "../../models/member/Member"
import { RegisterationService } from "../../services/RegisterationService";

@Component({
  selector: 'page-registration',
  templateUrl: 'registration.html'
})

export class RegistrationPage {

  constructor(private registerationService: RegisterationService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad RegistrationPage');
  }

  

  onAddMember(form: NgForm) {
    console.log('before create Member RegistrationPage');
    this.registerationService.createMember("bhatvisu1000", form.value.firstName, form.value.lastName, "visu", form.value.mobileNo, form.value.zipCode, form.value.emailAddress);
    console.log('before submit RegistrationPage');
    this.registerationService.submitMember();
    console.log('before after RegistrationPage');
    
  }
}
