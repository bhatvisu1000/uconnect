import { Address } from "./Address";
import { Contact } from "./Contact";
import { Main } from "./Main";

export class Connections {
  constructor(public address: Address, public Blocked: string, public contact: Contact, public Favorite: string, public Id: string, public main: Main, public Status: string, public Type: string, public Action: string) {}
}