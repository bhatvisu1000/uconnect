import { Summary } from "./Summary";


export class Header {
  constructor(public Status: string, public Message: string, public Traceback: string, public Summary: Summary) {}
}