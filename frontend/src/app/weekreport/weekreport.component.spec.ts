import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeekreportComponent } from './weekreport.component';

describe('Weekreport', () => {
  let component: WeekreportComponent;
  let fixture: ComponentFixture<WeekreportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeekreportComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WeekreportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
