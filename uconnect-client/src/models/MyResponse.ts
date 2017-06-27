import { Header } from "./response/Header";
import { Data } from "./response/Data";

export class MyResponse {
  constructor(public Header: Header, public Data: Data) {}
}