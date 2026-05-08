import { Component, OnInit } from '@angular/core';
import { ThemeService } from './shared/services/theme.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  title = 'Digital Banking - Shell Application';

  constructor(private themeService: ThemeService) {}

  ngOnInit(): void {
    // Apply VRGT theme on app initialization
    this.themeService.applyVRGTTheme();
  }
}
