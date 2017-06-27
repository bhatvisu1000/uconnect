import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';


@Injectable()
export class SQLStorageService {

constructor(private storage: Storage) {}

	put(key: string, value: string): void  {
		  
          this.storage.set(key, value);
	}
}