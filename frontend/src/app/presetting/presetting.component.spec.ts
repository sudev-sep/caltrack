import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PresettingComponent } from './presetting.component';

describe('PresettingComponent', () => {
  let component: PresettingComponent;
  let fixture: ComponentFixture<PresettingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PresettingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PresettingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
