'use strict';

var gulp = require('gulp');
var jshint = require('gulp-jshint');
var serve = require('gulp-serve');
var sass = require('gulp-ruby-sass');

gulp.task('build', ['build-css']);

gulp.task('build-css', function () {
    return sass('src/**/*.scss', {emitCompileError: true})
        .pipe(gulp.dest('build'));
});

gulp.task('lint', ['lint-node', 'lint-frontend']);

gulp.task('lint-frontend', function () {
    return gulp.src('src/**/*.js')
        .pipe(jshint({
            laxbreak: true
        }))
        .pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('lint-node', function () {
    return gulp.src('*.js')
        .pipe(jshint({
            node: true
        }))
        .pipe(jshint.reporter('jshint-stylish'));
});

gulp.task('server', ['build'], serve({
    root: ['bower_components', 'build', 'server', 'src'],
    port: 8000
}));
