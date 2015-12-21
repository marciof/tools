'use strict';

var gulp = require('gulp');
var jshint = require('gulp-jshint');
var serve = require('gulp-serve');

gulp.task('lint-node', function () {
    return gulp.src('*.js')
        .pipe(jshint({
            node: true
        }))
        .pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('lint-src', function () {
    return gulp.src('src/**/*.js')
        .pipe(jshint({
            laxbreak: true
        }))
        .pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('lint', ['lint-node', 'lint-src']);

gulp.task('server', serve({
    root: ['bower_components', 'src'],
    port: 8000
}));
