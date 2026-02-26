import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { PresettingComponent,} from './presetting/presetting.component';
import { RegisterComponent } from './register/register.component';
import { GoalsetComponent } from './goalset/goalset.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './guards/auth.guard';
import { WeekreportComponent } from './weekreport/weekreport.component';



export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    {path: 'home',component: HomeComponent, canActivate: [AuthGuard] },
    {path: 'presetting', component: PresettingComponent},
    {path: 'register', component: RegisterComponent},
    { path: 'goalset', component: GoalsetComponent},
    { path: 'login', component: LoginComponent},
    { path: 'weekreport', component: WeekreportComponent},

    

];
